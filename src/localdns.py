#coding=utf-8
from twisted.internet import error, defer, protocol, reactor
from twisted.names import common, dns, hosts, resolve, server
from twisted.python import failure
from twisted.internet.endpoints import TCP4ClientEndpoint
from txsocksx.client import SOCKS5ClientEndpoint
import logging
import config
import socket

class ResolverBase(common.ResolverBase):
    def __init__(self, proxy, servers):
        self.proxy = proxy
        self.servers = servers
        common.ResolverBase.__init__(self)
    
    def getHostByName(self, name, timeout=None, effort=10):
        deferred = self.lookupAllRecords(name, timeout)
        deferred.addCallback(self._cbRecords, name, timeout, effort)
        return deferred
    
    def _cbRecords(self, records, name, timeout, effort):
        (answers, authority, additional) = records
        result = self._extractRecord(answers + authority + additional, name, timeout, effort)
        if not result:
            raise error.DNSLookupError(name)
        return result
    
    def _extractRecord(self, records, name, timeout, effort):
        dnsName = dns.Name(name)
        
        if not effort:
            return None
        for r in records:
            if r.name == dnsName and r.type == dns.A:
                return socket.inet_ntop(socket.AF_INET, r.payload.address)
        for r in records:
            if r.name == dnsName and r.type == dns.A6:
                return socket.inet_ntop(socket.AF_INET6, r.payload.address)
        for r in records:
            if r.name == dnsName and r.type == dns.AAAA:
                return socket.inet_ntop(socket.AF_INET6, r.payload.address)
        for r in records:
            if r.name == dnsName and r.type == dns.CNAME:
                result = self._extractRecord(records, str(r.payload.name), timeout, effort - 1)
                if not result:
                    return self.getHostByName(str(r.payload.name), timeout, effort - 1)
                return result
        for r in records:
            if r.type == dns.NS:
                resolver = ServerResolver(self.proxy, str(r.payload.name), dns.PORT)
                return resolver.getHostByName(name, timeout, effort - 1)

class DNSProtocolClientFactory(protocol.ReconnectingClientFactory):
    def __init__(self, controller):
        self.controller = controller
    
    def clientConnectionLost(self, connector, reason):
        logging.error("DNSProtocolClientFactory.clientConnectionLost, reason: %s", reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        logging.error("DNSProtocolClientFactory.clientConnectionFailed, reason: %s", reason)
        
        deferreds = self.controller.deferreds[:]
        del self.controller.deferreds[:]
        for deferred, name, type, cls, timeout in deferreds:
            deferred.errback(reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
    
    def buildProtocol(self, addr):
        logging.debug("DNSProtocolClientFactory.buildProtocol")
        p = dns.DNSProtocol(self.controller)
        p.factory = self
        return p

class DnsOnTcpResolver(ResolverBase):
    def __init__(self, proxy, servers):
        ResolverBase.__init__(self, proxy, servers)

        self.i = 0
        self.proxy = proxy
        self.connections = []
        self.deferreds = []
        self.factory = DNSProtocolClientFactory(self)
    
    def connectionMade(self, connection):
        self.connections.append(connection)
        
        deferreds = self.deferreds[:]
        del self.deferreds[:]
        for (deferred, name, type, cls, timeout) in deferreds:
            self._lookup(name, cls, type, timeout).chainDeferred(deferred)
    
    def connectionLost(self, connection):
        self.connections.remove(connection)
    
    def messageReceived(self, message, protocol, address=None):
        pass

    def _lookup(self, name, cls, type, timeout=None):
        if not len(self.connections):
            self.i = (self.i + 1) % len(self.servers)

            server = self.servers[self.i]
            proxy_addr, proxy_port = self.proxy
            server_addr, server_port = server
            proxyEndpoint = TCP4ClientEndpoint(reactor, proxy_addr, proxy_port)
            dnsEndpoint = SOCKS5ClientEndpoint(server_addr, server_port, proxyEndpoint)

            dnsEndpoint.connect(self.factory)
            
            deferred = defer.Deferred()
            self.deferreds.append((deferred, name, type, cls, timeout))
            return deferred
        else:
            deferred = self.connections[0].query([dns.Query(name, type, cls)])
            deferred.addCallback(self._cbMessage)
            return deferred
    
    def _cbMessage(self, message):
        if message.rCode != dns.OK:
            return failure.Failure(self.exceptionForCode(message.rCode)(message))
        
        return (message.answers, message.authority, message.additional)

def build_dns():
    resolver = DnsOnTcpResolver(
            proxy=('127.0.0.1', config.CLIENT_PORT),
            servers=config.REMOTE_DNS_SERVICE_ADDRS)
    factory = server.DNSServerFactory(clients=[resolver], verbose=0)
    reactor.listenUDP(config.LOCAL_DNS_SERVICE_UDP_PORT, dns.DNSDatagramProtocol(factory))
    reactor.listenTCP(config.LOCAL_DNS_SERVICE_TCP_PORT, factory)

if __name__ == '__main__':
    build_dns()
    reactor.run()

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: packet.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='packet.proto',
  package='Melkweg',
  syntax='proto3',
  serialized_pb=_b('\n\x0cpacket.proto\x12\x07Melkweg\"o\n\x07MPacket\x12\n\n\x02iv\x18\x01 \x01(\x0c\x12\x0c\n\x04port\x18\n \x01(\r\x12\r\n\x05\x66lags\x18\x0b \x01(\r\x12\x0c\n\x04\x64\x61ta\x18\x0c \x01(\x0c\x12\x0f\n\x07padding\x18\r \x01(\x0c\x12\x0c\n\x04user\x18\x14 \x01(\t\x12\x0e\n\x06secret\x18\x15 \x01(\tb\x06proto3')
)




_MPACKET = _descriptor.Descriptor(
  name='MPacket',
  full_name='Melkweg.MPacket',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='iv', full_name='Melkweg.MPacket.iv', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='port', full_name='Melkweg.MPacket.port', index=1,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flags', full_name='Melkweg.MPacket.flags', index=2,
      number=11, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='Melkweg.MPacket.data', index=3,
      number=12, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='padding', full_name='Melkweg.MPacket.padding', index=4,
      number=13, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='user', full_name='Melkweg.MPacket.user', index=5,
      number=20, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='secret', full_name='Melkweg.MPacket.secret', index=6,
      number=21, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=136,
)

DESCRIPTOR.message_types_by_name['MPacket'] = _MPACKET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

MPacket = _reflection.GeneratedProtocolMessageType('MPacket', (_message.Message,), dict(
  DESCRIPTOR = _MPACKET,
  __module__ = 'packet_pb2'
  # @@protoc_insertion_point(class_scope:Melkweg.MPacket)
  ))
_sym_db.RegisterMessage(MPacket)


# @@protoc_insertion_point(module_scope)

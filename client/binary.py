"""

- CSH Server 'binary.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""

# Partially obtained from CFX internal module 'SERIALIZER'.


# ---------- IMPORTS ----------

from .misc import *


# ---------- FUNCTIONS ----------


# --- Serialization Functions ---

def serialize_int(data):

	"""Serialize an integer value."""

	size = (data.bit_length() + 7) // 8 + 1
	return int.to_bytes(data, size, byteorder='little', signed=True)

def serialize_float(data):

	"""Serialize a floating point value."""

	return struct.pack('f', data)

def serialize_string(data):

	"""Serialize a string."""

	return bytes(data, ENCODING)

def serialize_bytes(data):

	"""Serialize bytes."""

	return bytes(data)

def serialize_list(data):

	"""Serialize a list."""

	return b''.join([serialize(i) for i in data])

def serialize_tuple(data):

	"""Serialize a tuple."""

	return serialize_list(list(data))

def serialize_dict(data):

	"""Serialize a dict."""

	to_serialize = list(data.items())

	return serialize(to_serialize)

def serialize_none(data):

	"""Serialize a None."""

	return b'\x00'

def serialize_bool(data):

	"""Serialize a boolean."""

	return b'\x01' if data else b'\x00'

def serialize_set(data):

	"""Serialize a set."""

	return serialize_list(list(data))


# --- Deserialization Functions ---

def deserialize_int(data):

	"""Deserialize an integer value."""

	return int.from_bytes(data, byteorder='little', signed=True)

def deserialize_float(data):

	"""Deserialize a floating point value."""

	return struct.unpack('f', data)[0]

def deserialize_string(data):

	"""Deserialize a string."""

	return str(data, ENCODING)

def deserialize_bytes(data):

	"""Deserialize bytes."""

	return bytes(data)

def deserialize_list(data):

	"""Deserialize a list."""

	deserialized_list = []

	i = 0
	while i < len(data):
		data_type = data[i]
		function = TAG_MAP[data_type]
		i += 1

		data_length = int.from_bytes(data[i : i + 8], byteorder='little', signed=False)
		i += 8

		data_bytes = data[i : i + data_length]
		i += data_length

		deserialized_list.append(function(data_bytes))

	return deserialized_list

def deserialize_tuple(data):

	"""Deserialize a tuple."""

	return tuple(deserialize_list(data))

def deserialize_dict(data):

	"""Deserialize a dict."""

	ditems = deserialize(data)
	deserialized_dict = {}
	
	for key, val in ditems:
		deserialized_dict[key] = val

	return deserialized_dict

def deserialize_none(data):

	"""Deserialize a None."""

	return None

def deserialize_bool(data):

	"""Serialize a None."""

	return True if data == b'\x01' else False

def deserialize_set(data):

	"""Deserialize a set."""

	return set(deserialize_list(data))


# --- Type Map ---

TYPE_MAP = {int : [serialize_int, b'\x00'], 
			float : [serialize_float, b'\x01'],
			str : [serialize_string, b'\x02'],
			bytes : [serialize_bytes, b'\x03'],
			bytearray : [serialize_bytes, b'\x03'], # Bytes and bytearray correspond to the same function and tag
			list : [serialize_list, b'\x04'],
			tuple : [serialize_tuple, b'\x05'],
			dict : [serialize_dict, b'\x06'],
			type(None) : [serialize_none, b'\x07'],
			bool : [serialize_bool, b'\x08'],
			set : [serialize_set, b'\x09']}

TAG_MAP = {0 : deserialize_int,
		   1 : deserialize_float,
		   2 : deserialize_string,
		   3 : deserialize_bytes,
		   4 : deserialize_list,
		   5 : deserialize_tuple,
		   6 : deserialize_dict,
		   7 : deserialize_none,
		   8 : deserialize_bool,
		   9 : deserialize_set}


# --- Serialization ---

def serialize(data):

	"""Serialize an object.
	   Args: data -> Object to serialize."""

	try:
		# Get the object type and corresponding function and tag
		function, tag = TYPE_MAP[type(data)]
		serialized = function(data)

		# Return the tag with the serialized data
		return tag + int.to_bytes(len(serialized), 8, byteorder='little', signed=False) + serialized

	except Exception as e:
		# Serialization error
		raise SerializingException(str(e))


# --- Deserialization ---

def deserialize(data):

	"""Deserialize an object.
	   Args: data -> Bytes to deserialize."""

	try:
		# Get the data tag
		data_type = data[0]

		# Get the length of the data
		data_len = int.from_bytes(data[1 : 9], byteorder='little', signed=False)

		# Get the bytes of the data to deserialize
		data_bytes = data[9 : 9 + data_len]

		# Get the corresponding deserialization function
		function = TAG_MAP[data_type]

		# Attempt to deserialize and return
		return function(data_bytes)

	except Exception as e:
		# Deserialization error
		raise DeserializingException(str(e))

"""Super useful library for Python object validation"""

__version__ = "1.0.1"

import inspect # for more function validation later
import copy
from typing import Union

AnyNumber = Union[int, float]

class Object:
	"""Creates an object with the properties in `proto`"""
	def __init__(self, proto: dict):
		for key, value in proto.items():
			if type(value) is dict:
				value = Object(value)

			if type(value) is list:
				value = copy.deepcopy(value)
				for i, val in enumerate(value):
					if type(val) is dict: value[i] = Object(val)

			self.__dict__[key] = value

class Number:
	def __init__(self, *, max: AnyNumber=None, min: AnyNumber=None) -> None:
		self.high = max
		self.low = min

class Int(Number): pass

class Float(Number): pass

class LenableIterable:
	def __init__(self, *, max_len: int=None, min_len: int=0, elem_type: type=None):
		self.max_len = max_len
		self.min_len = min_len
		self.element_type = elem_type

class String(LenableIterable):
	def __init__(self, *, max_len: int=None, min_len: int=0, containsany: tuple[str]=None):
		self.max_len = max_len
		self.min_len = min_len
		self.contains = containsany

class Type:
	def __init__(self, proto: dict[str]=None, classattrs: dict[str]=None) -> None:
		self.proto = proto
		self.classattrs = classattrs

	def _numcheck(self, val: AnyNumber, high: AnyNumber, low: AnyNumber) -> bool:
		if (low is not None) and (val < low): return True
		if (high is not None) and (val > high): return True

	def verify_vars(self, obj: object) -> bool:
		if self.proto is None: return True

		props = {
			key: value for key, value in obj.__dict__.items() if not key.startswith('_')
		}

		if len(props) > len(self.proto): return False

		for key, value in self.proto.items():
			if key not in props: return False

			val = props[key]

			# check str, int, etc.
			if type(value) is String:
				if type(val) is not str: return False

				if (value.contains is not None):
					for string in value.contains:
						if string in val: break
						
					else: return False

				if (value.max_len is not None) and not (value.min_len <= len(val) <= value.max_len): return False
				if len(val) < value.min_len: return False

				continue

			if type(value) is LenableIterable:
				if (value.max_len is not None) and not (value.min_len <= len(val) <= value.max_len): return False
				if len(val) < value.min_len: return False

				if value.element_type is not None:
					for elem in val:
						if not Type({ "elem": value.element_type }).verify_vars(Object({ "elem": elem })): return False

				continue

			if type(value) is Number:
				if type(val) not in (int, float): return False

				if self._numcheck(val, value.high, value.low): return False

				continue

			if type(value) is Int:
				if type(val) is not int: return False

				if self._numcheck(val, value.high, value.low): return False

				continue
			
			if type(value) is Float:
				if type(val) is not float: return False

				if self._numcheck(val, value.high, value.low): return False

				continue

			if type(value) is dict:
				if not Type(value).verify_vars(val): return False

				continue

			if type(value) is Type:
				if not value.verify_vars(val): return False
				continue

			if type(value) is list:
				if type(val) is not list: return False

				if not Type(
					{
						str(i): item for i, item in enumerate(value)
					}
				).verify_vars(
					Object(
						{
							str(i): item for i, item in enumerate(val)
						}
					)
				): return False

				continue

			if type(val) is not value: return False

		return True


	def verify_classattrs(self, obj: object) -> bool:
		if self.classattrs is None: return True

		props = {
			key: value for key, value in obj.__class__.__dict__.items() if not key.startswith('_')
		}

		if len(props) > len(self.classattrs): return False

		for key, value in self.classattrs.items():
			if key not in props: return False

			val = props[key]

			if type(val) is property:
				val = getattr(obj, key)
				if (
					not Type(
						{ "prop": value }
					)
					.verify_vars(
						Object(
							{ "prop": val },
						)
					)
				): return False

				continue

			if type(value) is Type:
				if not value.verify_classattrs(val): return False
				continue

			if type(val) is not value: return False

		return True

	def verify(self, obj: object):
		return self.verify_vars(obj) and self.verify_classattrs(obj)
	
def verify(obj: object, proto: dict=None, class_proto: dict=None):
	return Type(proto, class_proto).verify(obj)
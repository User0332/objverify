from types import FunctionType
from objverify import (
	Object, 
	String, 
	Int,
	Type
)

Person_T = Type(
	{
		"name": String(max_len=12),
		"age": Int(min=20, max=100),
		"stats": {
			"DOB": String(min_len=6, max_len=8, containsany=('/',))
		}
	},
	{ "say_hello": FunctionType }
)

class Person:
	def __init__(self, name: str, age: int, stats: dict):
		self.name = name
		self.age = age
		self.stats = Object(stats)

	def say_hello(self):
		print(f"Hello! My name is {self.name} and I am {self.age} years old.")

person = Person("John Smith", 23, { "DOB": "1/12/22" })

if Person_T.verify(person):
	print("The person is a valid object!")
else:
	print("The person is not a valid object :(")
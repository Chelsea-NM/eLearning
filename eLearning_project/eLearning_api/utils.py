# I wrote this code
from enum import IntEnum

class Status(IntEnum):
  undefined = 0
  Active = 10
  Blocked = 40
  Archived = 50
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]
  
class CourseMaterialType(IntEnum):
  Generic = 0
  Image = 10
  Pdf = 20
  Word = 30
  Excel = 40
  Csv = 50
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]
  
class UserContactStatus(IntEnum):
  undefined = 0
  Active = 10
  Invited = 20
  Archived = 50
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]

# end of code I wrote
from typing import TypedDict

class ExecMessage(TypedDict):
  code: str
  data: dict

class ContMessage(TypedDict):
  pactId: str
  step: int
  rollback: bool
  data: dict
  proof: str

class ExecPayload(TypedDict):
  exec: ExecMessage

class ContPayload(TypedDict):
  cont: ContMessage


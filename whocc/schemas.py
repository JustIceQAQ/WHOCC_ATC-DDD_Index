from pydantic import BaseModel, Field


class AtcL1234Format(BaseModel):
    code: str
    name: str
    url: str


class AtcL5Format(BaseModel):
    code: str = Field(alias="ATC code", default=None)
    name: str = Field(alias="Name", default=None)
    url: str
    ddd: str = Field(alias="DDD", default=None)
    u: str = Field(alias="U", default=None)
    adm_r: str = Field(alias="Adm.R", default=None)
    note: str = Field(alias="Note", default=None)

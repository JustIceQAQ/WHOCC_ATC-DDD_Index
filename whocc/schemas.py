from pydantic import BaseModel, Field


class AtcL1234Format(BaseModel):
    code: str
    name: str
    url: str


class AtcL5Format(BaseModel):
    code: str | None = Field(alias="ATC code", default=None)
    name: str | None = Field(alias="Name", default=None)
    url: str
    ddd: str | None = Field(alias="DDD", default=None)
    u: str | None = Field(alias="U", default=None)
    adm_r: str | None = Field(alias="Adm.R", default=None)
    note: str | None = Field(alias="Note", default=None)

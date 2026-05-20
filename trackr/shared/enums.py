from enum import Enum


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class CompanyIndustry(str, Enum):
    LOGISTICS = "logistics"
    RETAIL = "retail"
    FMCG = "fmcg"
    PHARMA = "pharma"
    REAL_ESTATE = "real_estate"
    INSURANCE = "insurance"
    TELECOM = "telecom"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    OTHER = "other"

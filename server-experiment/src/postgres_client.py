from sqlalchemy import create_engine

def transform_payload(payload: dict[str, object], entry_type: str) -> dict[str, object]:
    result_dict = {}
    for k in payload:
        if k == "id":
            result_dict[entry_type] = payload[k]
        elif k == "created_at":
            result_dict["create_at"] = payload[k]
        elif k == "updated_at":
            result_dict["update_at"] = payload[k]
        else:
            result_dict[k] = payload[k]
    return result_dict

def transform_payload_experiment(payload: dict[str, object]) -> dict[str, object]:
    return transform_payload(payload, "id_experiment")

def transform_payload_workflow(payload: dict[str, object]) -> dict[str, object]:
    return transform_payload(payload, "id_workflow")

config = {
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_DB": "extremexp",
    "POSTGRES_HOST": "postgresql",
    "POSTGRES_PORT": "5432",
}
database_url = (f"postgresql://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}"
                f"@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_DB']}")

postgres_engine = create_engine(database_url, pool_pre_ping=True)
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # aws_creds: Optional[AWSCredentials]
    # log_level: str = 'DEBUG'
    env: str
    project_path: str
    microsoft_teams_webhook: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


settings = Config()

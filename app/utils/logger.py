import logging

logging.basicConfig(
    level=logging.INFO,
    format="""%(asctime)s.%(msecs)d %(levelname)-8s[%(filename)s:%(funcName)s:%(lineno)d] %(message)s""",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.disable(level=logging.DEBUG)
logger = logging.getLogger("app")

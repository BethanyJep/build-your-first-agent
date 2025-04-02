import json
import prompty
from pathlib import Path
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# add console and json tracer:
# this only has to be done once
# at application startup
Tracer.add("console", console_tracer)
json_tracer = PromptyTracer()
Tracer.add("PromptyTracer", json_tracer.tracer)

# if your prompty file uses environment variables make
# sure they are loaded properly for correct execution

@trace
def run(    
      title: any,
      tags: any,
      description: any
) -> str:

  # execute the prompty file
  result = prompty.execute(
    "basic.prompty", 
    inputs={
      "title": title,
      "tags": tags,
      "description": description
    }
  )

  return result

if __name__ == "__main__":
   base = Path(__file__).parent

   title = ("Including Image in System Message")
   description = ("An error arises in the flow, coming up starting from the complete block. It seems like it is caused by placing a static image in the system prompt, since removing it causes the issue to go away. Please let me know if I can provide additional context.")
   tags = json.loads(Path(base, "tags.json").read_text())

   result = run(title, tags, description)
   print(result)

import json
import prompty
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer

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
      description: any
) -> str:

  # execute the prompty file
  result = prompty.execute(
    "basic.prompty", 
    inputs={
      "title": title,
      "description": description
    }
  )

  return result

if __name__ == "__main__":
   json_input = '''{
  "title": "Including Image in System Message",
  "description": "An error arises in the flow, coming up starting from the \"complete\" block. It seems like it is caused by placing a static image in the system prompt, since removing it causes the issue to go away. Please let me know if I can provide additional context."
}'''
   args = json.loads(json_input)

   result = run(**args)
   print(result)

# mogop


Often encountered problems:

Kibana wont recognise timestamp on new index.

Solution:
# Make sure the index isn't there
DELETE /sandbox

# Create the index
PUT /sandbox

# Add the mapping of properties to the document type `mem`
PUT /sandbox/_mapping/mem
{
  "mem": {
    "properties": {
      "tstamp": {
        "type": "date"
      },
      "free": {
         "type": "long"
      }
    }
  }
}

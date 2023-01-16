# prometheus
Bringing FHIR to researchers

Promethius is a basic reverse proxy to provide access to public data hosted in a Google Cloud Healthcare service which normally requires authentication to access. The backend server being "exposed" should only ever have publicly accessible information in it which is not typical of traditional FHIR use-cases--thus the need to overcome google's requirements for authenticated access. 

## Google Only
When working to get the google stuff working, it became clear that none of the generic docker stuff was relevant, so I got rid of it. However, it's a simple application overall, so that shouldn't be much of a problem. 

## Application Notes
### GET Only
At the time of writing this (very early stages), the application ignores anything other than GET. 

### Service Account
Each GAE project gets it's own service account, which is the default. This is currently set up to use that default service account. It can be modified later on if need be. 

In order to permit access to the FHIR server via this particular account, it had to be added to the service's permissions. 

### Authentication Mechanism
The authentication queries the metadata server for a token via the REST API. An easy optimization will be to cache that token for the hour it is valid to avoid the extra REST call.(I believe that's the life-expectancy...but will need to double check that...)

### Standard vs Flexible Environment
Because our service is unlikely to be used with high regularity, it has been configured to use the "Standard Environment". This appears to bring the server up on demand and wind it back down after 15 minutes of inactivity. This is _probably_ what we want, but we can switch to use the "flexible environment" which will allow us to run it all the time with manually configured resources. Because of the up/down nature of these services, it will take longer for that first response than subsequent queries each time it is taken back down. 


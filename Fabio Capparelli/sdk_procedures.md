PROCEDURES:

1. Write on shell or cmd this command for python libraries -> pip install spotipy
2. Go to spotify for developpers -> https://developer.spotify.com/
3. Go to /dashboard -> https://developer.spotify.com/dashboard/
4. Create your application clicking on button -> "create new project"
--------------------------------------------------------------------------------
My credential, accessing through facebook:

- Client ID     -> 4b7a6ff9e9e242208bcb12834b0244ac
- Client Secret -> 786b8540a1c74b3491db3f8f1170185d

--------------------------------------------------------------------------------
5. Log in using one of these flows:
--------------------------------------------------------------------------------
https://developer.spotify.com/documentation/general/guides/authorization-guide/

supported by spotipy:

- Authorization Code Flow -> This flow is suitable for long-running applications in which the user grants permission only once. It provides an access token that can be refreshed. Since the token exchange involves sending your secret key, perform this on a secure location, like a backend service, and not from a client such as a browser or from a mobile app.

- Client Credentials Flow -> The method makes it possible to authenticate your requests to the Spotify Web API and to obtain a higher rate limit than you would with the Authorization Code flow.

FOR OUR SCOPE WE HAVE TO USE THE "Client Credential Flow"

![Cattura](https://user-images.githubusercontent.com/59933159/109431293-0fe52500-7a06-11eb-8463-8c7ff814f96e.PNG)

--------------------------------------------------------------------------------
  


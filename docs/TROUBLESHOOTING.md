# Common resolutions to lots of problems
If you are having trouble with something not working the first time, try these steps **in this order**:

1. Make sure the submodule(s) is in sync with the branch you are on:
```
git submodule update
```
2. Rebuild the image
```
docker-compose up --build
```
If the problem persists, then you'll need to look at it a little more closely.

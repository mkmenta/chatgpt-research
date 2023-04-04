# build with 
# docker build . -t  mkmenta/chatgpt-research
docker run --env-file .env -p 5000:5000 mkmenta/chatgpt-research
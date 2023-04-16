# ChatGPT Research
1. Install docker
2. Set the environment variables:
    - MONGOURI
    - OPENAI_API_KEY
    - OPENAI_ORGANIZATION
    - CHATGPT_RESEARCH_SECRET
    - NWORKERS (number of cpus)
3. Modify `nginx/conf/nginx.conf` changing:
    - `chatresearch.it` by your domain.
    - Removing the part `server { listen 443 ...}` temporarily.
4. Run `docker compose up --build`
5. Test certbot to get your certificates with:
```
docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d example.org -d www.example.org
```
6. If it works fine, run the same command without `--dryrun`
7. Bring back to `nginx/conf/nginx.conf` the part of `server { listen 443 ...}`
8. Run `docker compose up --build` again. (Maybe run `docker compose down first`).

For certificate renewal:
```
docker compose run --rm certbot renew
```

## References
- https://stackoverflow.com/questions/10938360/how-many-concurrent-requests-does-a-single-flask-process-receive
- https://mindsers.blog/post/https-using-nginx-certbot-docker/
## TODO:
- https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
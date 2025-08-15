# Tests

Simple tests.

2 dockers:
- jellyfin (linuxserver)
- jellyhookapi

Steps:

- you need to create the necessary folders for jellyfin:

`mkdir -p jellyfin/{config,data/movies}`

- you need to clone jellyhookapi, replace by this docker-compose file
- move the jellyhook docker compose in the root folder of jellyhookapi
- you need to edit the .env files.
- configure your desired connector (delete the useless ones)
- configure jellyfin
- add webhook plugin
- restart jellyfin
- configure webhook plugin
- create a movie (for exemple) folder and add your movie file into it.
- go to schedule tasks in jellyfin, run "analyze librairies" and then "webhook item added notifier"
- you should receive a notification

If you want to try again, just delete the movie (not the folder), run "analyze libraires".
You can now add your file again and repeat the previous steps.

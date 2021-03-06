# Meeting Room Remover

Meeting Room Remover is a Slackbot that allows users to remove meeting rooms from their events in Google Calendar when they are not in the office.

If the user has any meeting rooms booked for today AND she has not logged into Slack from the office IP address, the bot sends a message to the user. When the user clicks on a button, the bot removes the meeting room from the event.

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You have installed the docker and docker-compose

## Installing meeting-room-remover

To install meeting-room-remover, follow these steps:

```
git clone git@github.com:KosyanMedia/meeting-room-remover.git
cd meeting-room-remover
make up
```

## Using meeting-room-remover

To use meeting-room-remover, follow these steps:

```
* configuration steps TBD soon
* please, stay tuned 📻

```

Add run commands and examples you think users will find useful. Provide an options reference for bonus points!

## Contributing to meeting-room-remover
<!--- If your README is long or you have some specific process or steps you want contributors to follow, consider creating a separate CONTRIBUTING.md file--->
To contribute to meeting-room-remover, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin`
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contributors

Thanks to the following people who have contributed to this project:

* [@Yaroslav Kotyshov](https://github.com/kotyshov) 📖
* [@Anton Shalimov](https://github.com/AntonShalimov) 🐛
* [@Alexey Sergeev](https://github.com/SergeevAI) 🐛

## Contact

If you want to contact me you can reach us at [GH Issues](https://github.com/KosyanMedia/meeting-room-remover/issues)

## License

This project uses the following license: [<MIT>](<https://opensource.org/licenses/MIT>).

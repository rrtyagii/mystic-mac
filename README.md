<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url] -->
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/rrtyagii/mystic-mac">
    <img src="images/DALL·E 2022-08-10 17.40.59 - An astronaut lounging in a tropical resort in space, pixel art.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Mystic Mac</h3>

  <p align="center">
    WhatsApp chatbot powered by GPT3! Made to resolve your parent's technilogical questions. 
    <br />
    <a href="https://github.com/rrtyagii/mystic-mac"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/rrtyagii/mystic-mac">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div>

https://github.com/rrtyagii/mystic-mac/assets/47730677/98dbfa03-3752-4d8c-8b07-c8e8600f3c67

https://github.com/rrtyagii/mystic-mac/assets/47730677/9f43a673-18f7-46f7-88ed-405827525361

https://github.com/rrtyagii/mystic-mac/assets/47730677/ae8c3e69-9496-4ef7-9522-3cbb38dbbb39


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

I wanted to hack and create a chatbot for myself. Ended up dciding to make a whatsapp chatbot which connects to GPT-3.5-Turbo. This behaves somewhat like chat-gpt. I was insipired by [GOD IN A BOX](https://godinabox.co/). Do check them out!

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

<!-- This is an example of how to list things you need to use the software and how to install them. -->
* `python 3.9.16`
* Download `ngrok` from [https://ngrok.com/download](https://ngrok.com/download)
* Meta's developer account

### Installation

<!-- _Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._ -->

1. Get a free API Key and ORG Key at [https://openai.com](https://openai.com)
2. Clone the repo
   ```sh
   git clone https://github.com/rrtyagii/mystic-mac.git
   ```
3. Install Python packages and dependencies
   ```sh
   pip install -r requirements.txt
   ```
4. Enter your API in `web_server.py`
   ```py
   openai.organization = 'ENTER YOUR ORG KEY'
   openai.api_key='ENTER YOUR API KEY'
   meta_token = 'ENTER YOUR META ACCESS TOKEN'
   meta_app_secret = 'ENTER YOUR APP SECRET'  
   verification_token = 'ENTER YOUR OWN TOKEN TO VERIFY WEBHOOK'
   ```
5. Run the ngrok port
  ```sh
   ngrok http 5002
  ```
6. Run the `Flask` web server
  ```sh
  flask --app web_server.py run --debug --port 5002
  ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [ ] Support session history
- [ ] Reset Conversation after 10 minutes
- [ ] Add Speech to Speech response cabilities
- [ ] Multi-language Support on voice note messages
    - [ ] English
    - [ ] Spanish
- [ ] Information security (conversations, phone numbers, etc)

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Rishabh Tyagi - [@AllAuover](https://twitter.com/AllAuover) - rtyagi1@hawk.iit.edu

Project Link: [https://github.com/rrtyagii/mystic-mac](hhttps://github.com/rrtyagii/mystic-mac)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Img Shields](https://shields.io)
* [OpenAI](https://openai.com/)
* [GOD IN A BOX](https://godinabox.co/)
* [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!-- [contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/rrtyagii/mystic-mac/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues -->
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/rrtyagii/mystic-mac/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/rtyagi1/
[product-screenshot]: images/screenshot.png
[Flask]: https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white
[VS Code Insiders]: https://img.shields.io/badge/VS%20Code%20Insiders-35b393.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white

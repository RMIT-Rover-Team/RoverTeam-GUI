#
---
note: rm -rf the myenv and make new python3 env and source it to avoid externally managed env error


## whoa! this is so cool! how does this work?

-- NOTE: THIS SECTION IS TECHNICAL AND WILL THROW BIG WORDS AT YOU. keep up ;) --

This uses a real time streaming protocol called **WebRTC**, owned by Google. It's a new protocol used by popular voice applications like Google Meet, Discord, WhatsApp, etc. due to minimal latency and support for live streaming with video. This is what we use to communicate to the rover's cameras via radio.

It uses the **ICE (Interactive Connectivity Establishment)** framework which coordinates **STUN** and **TURN** (Session Traversal Utilities for NAT, Traversal Using Relays around NAT - NAT - Network Address Translation) which helps the discovery of public IP addresses to enable direct communication (also known as direct peer-to-peer connection).

The file responsible for all this magic is `rover_webrtc.py`, a Python script which uses the above methods to stream the camera connections via WebRTC. This script is located on the Raspberry Pi and acts as a "Host", and the file `index.tsx` (made using react - typescript) views the feed live.

Your computer, which is connected to the rover via radio, acts as a "client" and translates the NAT communication, which allows for real time video streaming to the cameras on the rover.

For my visual learners, see the diagram attached. **A** would be the client (e.g. someone's laptop) and **B** would be the Raspberry Pi.

![WebRTC Architecture Diagram](webrtc-gui/public/ivrpowers-turn-stun-screen.005.jpeg)
# Rover GUI - USB Cameras Example

![Rover GUI with USB Cameras](webrtc-gui/public/rover_gui_usb_cameras.png)

This screenshot shows the Rover GUI displaying two connected USB cameras, with live video feeds and connection status indicators.

in this case, Camera 0 is the camera below the right wheel (for payloads), and Camera 2 is the 360 Gimbal Camera. 


# How to clone the repository

Head to the repository: https://github.com/Ridge19/RoverTeam-GUI

**Cloning via SSH (most common and easiest):**
1. Click on 'Code' then copy the SSH URL: `git@github.com:Ridge19/RoverTeam-GUI.git`
2. In your terminal, run:

```bash
git clone git@github.com:Ridge19/RoverTeam-GUI.git
```

# How to run GUI

- On the laptop (client), open your editor of choice (e.g. VS Code) after cloning the repository (see above).
- After cloning, install dependencies using:

```bash
npm install
```
(Make sure you are in the `webrtc-gui` folder)
- To run the GUI application, use:

```bash
npm run dev
```
It will be accessible via [localhost:3000](http://localhost:3000)
You should see:

```text
> webrtc-gui@0.1.0 dev
> next dev --turbopack

▲ Next.js 15.4.6 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://172.24.80.1:3000
```

# Connecting cameras

- Go to the `webrtc-gui` folder, and run the script `rover_webrtc.py` using either:

```bash
python rover_webrtc.py
# OR
python3 rover_webrtc.py
```
- If successful, you should see:

```text
INFO:root:Starting rover server at http://0.0.0.0:3001
======== Running on http://0.0.0.0:3001 ========
(Press CTRL+C to quit)
```
- If you cannot run the script, install dependencies using:

```bash
pip install -r requirements.txt
```

# Checking cameras

- The backend makes it easy: head to [localhost:3000/cameras](http://localhost:3000/cameras) (on laptop)
on rover: http://192.168.50.1:3001/cameras
	- This will list all available USB cameras.
- If you are connected to a camera or if it is not detected (e.g. not plugged in), it will not show. Please ensure this is done (don't be like Ridge haha).

# Checking WebRTC server

- There is also a backend to check the WebRTC server: head to [localhost:3001](http://localhost:3001) (on laptop)
on rover: http://192.168.50.1:3001/
	- This is hosted on the rover and the laptop (client) is connected to the Pi (host).
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/pages/api-reference/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.tsx`. The page auto-updates as you edit the file.

[API routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes) can be accessed on [http://localhost:3000/api/hello](http://localhost:3000/api/hello). This endpoint can be edited in `pages/api/hello.ts`.

The `pages/api` directory is mapped to `/api/*`. Files in this directory are treated as [API routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes) instead of React pages.

This project uses [`next/font`](https://nextjs.org/docs/pages/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js and WebRTC, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn-pages-router) - an interactive Next.js tutorial.
- [WebRTC Documentation](https://webrtc.org/getting-started/overview) - learn about real-time streaming and peer-to-peer connections.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

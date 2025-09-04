# Rover GUI - USB Cameras Example

![Rover GUI with USB Cameras](public/rover_gui_usb_cameras.png)

This screenshot shows the Rover GUI displaying two connected USB cameras, with live video feeds and connection status indicators.


# How to run GUI

- On the laptop (client), open your editor of choice (e.g. VS Code) and clone the repository.
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
	```
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
	```
	INFO:root:Starting rover server at http://0.0.0.0:3001
	======== Running on http://0.0.0.0:3001 ========
	(Press CTRL+C to quit)
	```
- If you cannot run the script, install dependencies using:
	```bash
	pip install -r requirements.txt
	```

# Checking cameras

- The backend makes it easy: head to [localhost:3000/cameras](http://localhost:3000/cameras)
	- This will list all available USB cameras.
- If you are connected to a camera or if it is not detected (e.g. not plugged in), it will not show. Please ensure this is done (don't be like Ridge haha).

# Checking WebRTC server

- There is also a backend to check the WebRTC server: head to [localhost:3001](http://localhost:3001)
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

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn-pages-router) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/pages/building-your-application/deploying) for more details.

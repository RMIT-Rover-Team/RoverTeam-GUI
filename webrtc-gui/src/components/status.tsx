// component to show the current status of the rover

import { useState } from "react";

type StatusLed =
  | "interactive"
  | "motion"
  | "initiating automatic motion"
  | "automatic"
  | "locked"
  | "conflict"
  | "error";

type RoverStatusDetails = {
  name: string;
  description: string;
  colour: string;
  font_colour: string;
};

//all statuses the rover led with name, desc, colour and font colour
const statusRecord: Record<StatusLed, RoverStatusDetails> = {
  interactive: {
    name: "Interactive",
    description:
      "Safe interaction with rover is possible, rover is not going to start moving until light changes ",
    colour: " #ffffff",
    font_colour: "#222222",
  },
  motion: {
    name: "Motion",
    description: "Motion enabled, rover is under manual control",
    colour: "#6771ceff",
    font_colour: "#2d336bff",
  },
  "initiating automatic motion": {
    name: "Initiating...",
    description: "Will begin to move automatically soon",
    colour: "#67c0ceff",
    font_colour: "#2d666fff",
  },
  automatic: {
    name: "Automatic",
    description: "Currently carrying out an automatic program of movement",
    colour: "#a0ce67",
    font_colour: "#688c3bff",
  },
  locked: {
    name: "Locked",
    description: "Mechanically locked or otherwise inoperable",
    colour: "#cec967ff",
    font_colour: "#726e2cff",
  },
  conflict: {
    name: "Conflict",
    description:
      "Rover starting up, conflicting light state signals, or error with the indicator light",
    colour: "#cf67a9ff",
    font_colour: "#7e3262ff",
  },
  error: {
    name: "Error",
    description:
      "An error with the rover beyond the indicator light has occurred",
    colour: "#dd5555",
    font_colour: "#ac3c3cff",
  },
};

export default function Status({ status }: { status: StatusLed }) {
  const [currStatus, setCurrStatus] = useState<RoverStatusDetails>(
    statusRecord[status]
  );

  return (
    <>
      <div className="GUI-VFlex p-4">
        <text
          className="GUI-status rounded-[15px] p-2 text-center"
          style={{
            backgroundColor: currStatus.colour,
            color: currStatus.font_colour,
          }}
        >
          {currStatus.name}
        </text>
      </div>
    </>
  );
}

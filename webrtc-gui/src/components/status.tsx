// component to show the current status of the rover

type StatusLed =
  | "interactive"
  | "motion"
  | "initiating automatic motion"
  | "automatic motion"
  | "locked"
  | "conflict"
  | "error";

type RoverStatusDetails = {
  description: string;
  colour: string;
};

//all statuses the rover led could be
const statusRecord: Record<StatusLed, RoverStatusDetails> = {
  interactive: {
    description:
      "Safe interaction with rover is possible, rover is not going to start moving until light changes ",
    colour: " #ffffff",
  },
  motion: {
    description: "Motion enabled, rover is under manual control",
    colour: "#6771ceff",
  },
  "initiating automatic motion": {
    description: "Will begin to move automatically soon",
    colour: "#67c0ceff",
  },
  "automatic motion": {
    description: "Currently carrying out an automatic program of movement",
    colour: "#a0ce67",
  },
  locked: {
    description: "Mechanically locked or otherwise inoperable",
    colour: "#cec967ff",
  },
  conflict: {
    description:
      "Rover starting up, conflicting light state signals, or error with the indicator light",
    colour: "#cf67a9ff",
  },
  error: {
    description:
      "An error with the rover beyond the indicator light has occurred",
    colour: "#dd5555",
  },
};

export default function Status(currStatus: string) {
  return <></>;
}

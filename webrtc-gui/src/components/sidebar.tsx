// sidebar component shows important at glance information

import Clock from "./clock";
import Status from "./status";

export default function Sidebar() {
  return (
    <>
      <div className="GUI-sidebar gap-4">
        <Clock />
        <Status status="automatic" />
      </div>
    </>
  );
}

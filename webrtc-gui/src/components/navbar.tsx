interface NavbarProps {
  currPage: string;
  setCurrPage: (page: string) => void;
}

export default function Navbar({ currPage, setCurrPage }: NavbarProps) {
  return (
    <>
      <div className="GUI-HFlex h-[10vh] gap-16 p-[25px] w-[70vw] mt-8 items-center  ">
        <button
          onClick={() => setCurrPage("home")}
          className="GUI-navbar-button"
        >
          Home
        </button>
        <button
          onClick={() => setCurrPage("extraction")}
          className="GUI-navbar-button"
        >
          Extraction
        </button>
        <button
          onClick={() => setCurrPage("detection")}
          className="GUI-navbar-button"
        >
          Detection
        </button>
      </div>
    </>
  );
}

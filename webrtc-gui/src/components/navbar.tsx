interface NavbarProps {
  currPage: string;
  setCurrPage: (page: string) => void;
}

export default function Navbar({ currPage, setCurrPage }: NavbarProps) {
  return (
    <>
      <div className="GUI-HFlex h-[10vh] gap-16 p-[25px] w-[70vw] items-center  ">
        <button
          onClick={() => setCurrPage("home")}
          className={`GUI-navbar-button ${
            currPage === "home"
              ? "text-[#dd5555]"
              : "text-white hover:text-red-500"
          }`}
        >
          Home
        </button>
        <button
          onClick={() => setCurrPage("extraction")}
          className={`GUI-navbar-button ${
            currPage === "extraction"
              ? "text-[#dd5555]"
              : "text-white hover:text-red-500"
          }`}
        >
          Extraction
        </button>
        <button
          onClick={() => setCurrPage("detection")}
          className={`GUI-navbar-button ${
            currPage === "detection"
              ? "text-[#dd5555]"
              : "text-white hover:text-red-500"
          }`}
        >
          Detection
        </button>
      </div>
    </>
  );
}

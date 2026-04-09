import { useState } from "react";

export default function Tooltip({ text, children }: any) {
  const [show, setShow] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  const handleMouseEnter = (e: any) => {
    const rect = e.currentTarget.getBoundingClientRect();

    setPos({
      top: rect.top + rect.height / 2,
      left: rect.right + 10,
    });

    setShow(true);
  };

  return (
    <>
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={() => setShow(false)}
        style={{ display: "flex" }}
      >
        {children}
      </div>

      {show && text && (
        <div
          style={{
            position: "fixed", // 🔥 LA CLAVE
            top: pos.top,
            left: pos.left,
            transform: "translateY(-50%)",

            background: "#2d2d2d",
            color: "#fff",
            padding: "6px 10px",
            borderRadius: "6px",
            fontSize: "0.75rem",
            whiteSpace: "nowrap",

            boxShadow: "0 4px 10px rgba(0,0,0,0.25)",
            zIndex: 9999,
          }}
        >
          {text}
        </div>
      )}
    </>
  );
}
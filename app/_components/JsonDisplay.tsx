import React, { useEffect, useState } from "react";
import { List, ListRowProps } from "react-virtualized";
import { TurtleJsonType } from "../types";

interface JsonDisplayProps {
  data: TurtleJsonType;
}

const JsonDisplay: React.FC<JsonDisplayProps> = ({ data }) => {
  const [turtleJson, setTurtleJson] = useState<TurtleJsonType | null>(null);

  useEffect(() => {
    if (data) {
      setTurtleJson(data);
    }
  }, [data]);

  const copyToClipboard = async () => {
    if (turtleJson) {
      try {
        await navigator.clipboard.writeText(JSON.stringify(turtleJson));
        alert("JSONがクリップボードにコピーされました！");
      } catch (err) {
        console.error("コピーに失敗しました:", err);
      }
    }
  };

  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    if (!turtleJson) return null;
    const jsonData = [turtleJson.size, turtleJson.data];
    return (
      <div key={key} style={style} className="json-row">
        {JSON.stringify(jsonData[index], null, 2)}
      </div>
    );
  };

  return (
    <div className="json-container">
      <button onClick={copyToClipboard} className="copy-button">JSONをコピー</button>
      {turtleJson && (
        <List
          width={600}
          height={400}
          rowHeight={50}
          rowCount={2}
          rowRenderer={rowRenderer}
        />
      )}
    </div>
  );
};

export default JsonDisplay;
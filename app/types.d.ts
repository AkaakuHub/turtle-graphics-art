type TurtleCommand = 'u' | 'd' | `m${number}` | `r${number}` | `l${number}`;

interface TurtleJson {
  commands: TurtleCommand[];
}

export interface TurtleJsonType {
  size: [number, number];
  data: TurtleJson;
}
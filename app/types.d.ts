export type TurtleCommand = 'u' | 'd' | `m${number}` | `r${number}` | `l${number}`;

export interface TurtleCommands {
  commands: TurtleCommand[];
}

export interface TurtleJsonType {
  size: [number, number];
  data: TurtleJson;
}
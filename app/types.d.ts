export type TurtleCommand = 'u' | 'd' | `m${number}` | `r${number}` | `l${number}`;

export type TurtleCommands = TurtleCommand[];

export interface TurtleJsonType {
  size: [number, number];
  data: TurtleJson;
}
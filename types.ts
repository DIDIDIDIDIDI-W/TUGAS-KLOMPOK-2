
export type DataRow = Record<string, string | number>;

export interface RegressionResult {
  slope: number;
  intercept: number;
  rSquared: number;
  lineData: { x: number; y: number }[];
}

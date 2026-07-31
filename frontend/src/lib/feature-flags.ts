export const FEATURE_RECOMMENDATIONS =
  process.env.FEATURE_RECOMMENDATIONS === "false" ||
  process.env.NEXT_PUBLIC_FEATURE_RECOMMENDATIONS === "false"
    ? false
    : true;

export const FEATURE_REVIEWS =
  process.env.FEATURE_REVIEWS === "false" ||
  process.env.NEXT_PUBLIC_FEATURE_REVIEWS === "false"
    ? false
    : true;

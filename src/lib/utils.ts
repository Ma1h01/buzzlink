import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import defaultPic from "@/default-pic.png";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Validates an image URL and returns a fallback image if the URL is invalid
 * @param imageUrl - The URL of the image to validate
 * @param fallbackImage - The fallback image URL to use if the main image fails to load
 * @returns A Promise that resolves to either the original image URL or the fallback image URL
 */
export async function validateImageUrl(
  imageUrl: string,
  fallbackImage: string = defaultPic
): Promise<string> {
  if (!imageUrl) {
    return fallbackImage;
  }

  try {
    const response = await fetch(imageUrl, { method: "HEAD" });
    if (
      response.ok &&
      response.headers.get("content-type")?.startsWith("image/")
    ) {
      return imageUrl;
    }
    return fallbackImage;
  } catch (error) {
    console.error("Error validating image URL:", error);
    return fallbackImage;
  }
}

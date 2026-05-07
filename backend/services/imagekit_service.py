
from imagekitio import ImageKit
from config import IMAGEKIT_URL_ENDPOINT, IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY

ImageKit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY,
    public_key=IMAGEKIT_PUBLIC_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)

def upload_image(file_bytes :bytes, file_name: str, folder: str, content_type: str="image/png")->str:
  """Uploads an image to ImageKit and returns the URL of the uploaded image."""
  result = ImageKit.files.upload(
      file=(file_bytes, content_type, file_name),
      file_name=file_name,
      folder=folder,
      is_private_file=False,
      use_unique_file_name=True
  )
  return result.url

def get_variant_url(base_url: str)-> dict:
  """Returns 3 size variants of the image given the base URL."""
  return {
      "youtube": f"{base_url}?tr=w-1280,h-720,c-maintain_ratio,fo-auto",
      "shorts": f"{base_url}?tr=w-1080,h-1920,c-maintain_ratio,fo-auto",
      "square": f"{base_url}?tr=w-1080,h-1080,c-maintain_ratio,fo-auto"
  }
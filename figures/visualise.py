from vssutils import VssFileClient, VssDBClient, MovieSegment, RailSegmentView, VssVideoReader, FrameImage, VssClient, LocalSecrets, CameraSegment
from matplotlib import pyplot as plt
import cv2
from pandas import DataFrame
import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient


def concat_image(secrets: LocalSecrets, metadata: DataFrame):
    vss_client = VssClient('test', secrets)

    supplier = metadata.head(1).squeeze().supplier
    if supplier == 'eurailscout':
        vss_file_client = vss_client.eurailscout_vss_file_client
    elif supplier == 'asset-insight':
        vss_file_client = vss_client.asset_insight_vss_file_client
    else:
        raise NotImplementedError(f'Unknown supplier {supplier}')

    camera = CameraSegment(metadata)
    camera.retrieve_frames(vss_file_client)
    image = FrameImage.convert_bgr_to_rgb(camera.concat_frames())
    plt.figure(figsize=(200, 200))
    plt.imshow(image)
    plt.imsave("new.png", image)

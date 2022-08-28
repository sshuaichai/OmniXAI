import os
import unittest
import numpy as np
from torchvision import transforms
from PIL import Image as PilImage

from omnixai.data.image import Image
from omnixai.explainers.vision.specific.feature_visualization.pytorch.preprocess import RandomBlur


class TestPreprocess(unittest.TestCase):

    def setUp(self) -> None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../datasets")
        img = Image(PilImage.open(os.path.join(directory, "images/dog_cat.png")).convert("RGB"))
        transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor()
            ]
        )
        self.img = transform(img.to_pil())

    @staticmethod
    def _tensor_to_numpy(x):
        x = x.detach().cpu().numpy()
        x = np.swapaxes(np.swapaxes(x, 0, 1), 1, 2)
        return x

    def test_blur(self):
        transform = RandomBlur(kernel_size=9)
        y = transform.transform(self.img)

        import matplotlib.pyplot as plt
        plt.imshow(self._tensor_to_numpy(self.img))
        plt.show()
        plt.imshow(self._tensor_to_numpy(y))
        plt.show()


if __name__ == "__main__":
    unittest.main()

from .. import DataWrapper
from cogdl.backend import BACKEND

if BACKEND == "jittor":
    from cogdl.data.sampler_jt import UnsupNeighborSamplerDataset
elif BACKEND == "torch":
    from cogdl.data.sampler import UnsupNeighborSampler, UnsupNeighborSamplerDataset


class UnsupGraphSAGEDataWrapper(DataWrapper):
    @staticmethod
    def add_args(parser):
        # fmt: off
        parser.add_argument("--batch-size", type=int, default=128)
        parser.add_argument("--sample-size", type=int, nargs='+', default=[10, 10])
        # fmt: on

    if BACKEND == "jittor":

        def __init__(self, dataset, batch_size: int, sample_size: list):
            super(UnsupGraphSAGEDataWrapper, self).__init__(dataset)
            self.dataset = dataset
            self.train_dataset = UnsupNeighborSamplerDataset(
                dataset,
                sizes=sample_size,
                batch_size=batch_size,
                mask=dataset.data.train_mask,
                shuffle=False,
                data_shuffle=False,
            )
            self.val_dataset = UnsupNeighborSamplerDataset(
                dataset,
                sizes=sample_size,
                batch_size=batch_size * 2,
                mask=dataset.data.val_mask,
                shuffle=False,
                data_shuffle=False,
            )
            self.test_dataset = UnsupNeighborSamplerDataset(
                dataset=self.dataset,
                mask=None,
                sizes=[-1],
                batch_size=batch_size * 2,
                shuffle=False,
                data_shuffle=False,
            )
            self.x = self.dataset.data.x
            self.y = self.dataset.data.y
            self.batch_size = batch_size
            self.sample_size = sample_size

        def train_wrapper(self):
            self.dataset.data.train()
            return self.train_dataset

        def test_wrapper(self):
            return (self.dataset, self.test_dataset)

    elif BACKEND == "torch":

        def __init__(self, dataset, batch_size: int, sample_size: list):
            super(UnsupGraphSAGEDataWrapper, self).__init__(dataset)
            self.dataset = dataset
            self.train_dataset = UnsupNeighborSamplerDataset(
                dataset, sizes=sample_size, batch_size=batch_size, mask=dataset.data.train_mask
            )
            self.val_dataset = UnsupNeighborSamplerDataset(
                dataset, sizes=sample_size, batch_size=batch_size * 2, mask=dataset.data.val_mask
            )
            self.test_dataset = UnsupNeighborSamplerDataset(
                dataset=self.dataset,
                mask=None,
                sizes=[-1],
                batch_size=batch_size * 2,
            )
            self.x = self.dataset.data.x
            self.y = self.dataset.data.y
            self.batch_size = batch_size
            self.sample_size = sample_size

        def train_wrapper(self):
            self.dataset.data.train()
            return UnsupNeighborSampler(
                dataset=self.train_dataset,
                mask=self.dataset.data.train_mask,
                sizes=self.sample_size,
                num_workers=4,
                shuffle=False,
                batch_size=self.batch_size,
            )

        def test_wrapper(self):
            return (
                self.dataset,
                UnsupNeighborSampler(
                    dataset=self.test_dataset,
                    mask=None,
                    sizes=[-1],
                    batch_size=self.batch_size * 2,
                    shuffle=False,
                    num_workers=4,
                ),
            )

    def train_transform(self, batch):
        target_id, n_id, adjs = batch
        x_src = self.x[n_id]

        return x_src, adjs

    def get_train_dataset(self):
        return self.train_dataset

    def pre_transform(self):
        self.dataset.data.add_remaining_self_loops()

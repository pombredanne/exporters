from exporters.writers.base_writer import BaseWriter, ItemsLimitReached


class ConsoleWriter(BaseWriter):
    """
    It is just a writer with testing purposes. It prints every item in console.
    """

    def __init__(self, options):
        super(ConsoleWriter, self).__init__(options)
        self.logger.info('ConsoleWriter has been initiated')

    def write_batch(self, batch):
        for item in batch:
            print item.formatted
            self.stats['items_count'] += 1
            self.items_count += 1
            if self.items_limit and self.items_limit == self.stats['items_count']:
                raise ItemsLimitReached('Finishing job after items_limit reached: {} items written.'.format(self.stats['items_count']))
        self.logger.debug('Wrote items')
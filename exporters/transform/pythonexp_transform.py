from exporters.transform.base_transform import BaseTransform
from exporters.python_interpreter import Interpreter, DEFAULT_CONTEXT


class PythonexpTransform(BaseTransform):
    """
    It applies python expressions to items.

        - python_expression (str)
            Valid python expression
    """
    # List of options to set up the transform module
    supported_options = {
        'python_expressions': {'type': list}
    }

    def __init__(self, options):
        super(PythonexpTransform, self).__init__(options)
        self.python_expressions = self.read_option('python_expressions')
        if not self.is_valid_python_expression(self.python_expressions):
            raise ValueError('Python expression is not valid')
        self.interpreter = Interpreter()
        self.logger.info('PythonexpTransform has been initiated. Expressions: {!r}'.format(self.python_expressions))

    def transform_batch(self, batch):
        for item in batch:
            context = DEFAULT_CONTEXT.copy()
            context.update({'item': item})
            for expression in self.python_expressions:
                self.interpreter.eval(expression, context=context)
            yield item
        self.logger.debug('Transformed items')

    # TODO: Make a expression validator
    def is_valid_python_expression(self, python_expressions):
        return True

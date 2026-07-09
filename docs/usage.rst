Usage
=====

Creating a Hook
---------------

.. code-block:: python

    from teksi_hooks import HookBase, HookContext, HookMetadata


    class Hook(HookBase):
        required_capabilities = frozenset()

        @property
        def metadata(self) -> HookMetadata:
            return HookMetadata(
                name="Example Hook",
                description="Example implementation.",
            )

        def run_hook(self, context: HookContext) -> None:
            context.logger.info("Hello from a hook")

Executing a Hook
----------------

.. code-block:: python

    context = HookContext(
        parameters={},
        logger=logger,
        capabilities={},
    )

    HookHandler(
        file="example_hook.py",
    ).run(context)

Capabilities
------------

Capabilities are application-provided services.

.. code-block:: python

    service = context.capability(MyCapability)

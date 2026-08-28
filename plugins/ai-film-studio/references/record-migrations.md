# Record Migration Boundary

The canonical v0.1.0 interfaces are the eleven title-cased records indexed by `schemas/stable-record-interfaces.json`. Earlier draft `asset-record` and `shot-record` shapes were removed before installation because they had incompatible ownership fields and no declared migration path.

`ModelProfile` is the sole model-extension interface. The earlier draft `model-adapter` shape was also removed because it could not represent Kling, Veo, or future candidates consistently.

Auxiliary lower-case project, performance, geography, iteration, advisor, and delivery records remain internal supporting records. They do not replace or alias the stable interfaces. A future incompatible change must introduce a new schema version and an explicit migration fixture.

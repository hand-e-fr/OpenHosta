## **OpenHosta v1.2.0 - 10/14/24**

### **Features**
- Added the `predict` function, enabling internal model creation through linear regression.
- Introduced `.retrain` and `.continue_train` to allow dynamic model retraining and continued training.
- Introduced the `.emulate` function for generating predictions via LLM or internal models.
- Added new TrainingSet tools to manage datasets, including `.add` and `.visualize`.

### **Enhancements**
- Expanded file format support for loading datasets (JSON, JSONL, CSV).
- Enabled verbose mode in the `predict` function to track detailed training information.
- Added the `get_loss` attribute to control target loss during training.

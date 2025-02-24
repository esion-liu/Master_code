The 研究データ folder contains all the codes of the research.
Also, this folder contains most of the data expcet large language models' weights (>200GB), and the full database docker (>40GB) which are too big to be uploaded, usually data lies in second level folders 'data' or 'Dataset'
Defferent folders contains different set of experiments, summaried as follows:

steam_scrapy:
    The program to collect users' textual reviews from Steam Community
    environment:
        virtual environment manager: conda 24.1.2
        python version 3.10
        package installation: pip install scrapy
        postgresql database in the same host with port 5432 and corresponding database and tables (can be change to other place with need to change the setting.py and settings in datacleaning.ipynb)
    # if the website structure of Steam Community changed, the code is not guaranteed to work, but as tested in February 2025, it is still work.

NLP_Regression:
    This folder contains the experiments used in the thesis's section 4.2, about the bert sentiment regression model with steam dataset
    environment:
        virtual environment manager: conda 24.1.2
        python version 3.10
        package installation: pip install numpy matplotlib panda transformers torch torchvision
        same postgresql datasee as in steam_scrapy

llama_fitting:
    This folder contains the experiments used in the thesis's section 4.3, about llama3's finetuning, and experiment in the thesis's section 
    Also contains the inference process of the synthetic dataset from Doubao, which is the experiment in thesis's section 5.4
    Then, since the hardware failure of finetuning, llama3_ft_e301-500.ipynb was renamed from llama3_ft_e1-500, they are almost similar just 1-500 is finetuning from original model while 301-500 is from epoch 301.
    environment:
        follow the instruction https://docs.unsloth.ai/get-started/installing-+-updating/conda-install for the environment setup
        the environment should be linux, but in my experiment I used the WSL2 (Windows subsystem linux 2) with RTX 4090 and Nvidia driver version 471, but I think using linux could be more stable.

WorkSpace:
    Main WorkSpace for aggregation functions, CAPRA, MC-EM (R language), and RUMSA algorithms
    experiments for thesis's section 5.2 and 5.3 are included in this folder
    environment:
        virtual environment manager: conda 24.1.2
        python version 3.10
        package installation: pip install numpy matplotlib panda transformers torch torchvision
        compsoc library installation: pip install git+https://github.com/raviq/compsoc.git
        R version: 4.4.1
        R packages: StatRank



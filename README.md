# MvnFeed CLI

The _MvnFeed CLI_ is a command line interface to transfer artifacts from one Maven repository into another.

The tool has been developed to help teams use the Azure Artifacts infrastructure until the [upstream source for Maven feeds](https://visualstudio.uservoice.com/forums/330519-azure-devops-formerly-visual-studio-team-services/suggestions/32996752-add-upstream-sources-for-maven-feeds) is available.

The CLI downloads artifacts from one repository into a stage directory before uploading them onto the target repository.

## Installation

To install:

1. Ensure prerequisites are installed:
    * Python2 or 3

1. Check out the Git repository;

1. Run the install script:

    ```bash
    # python 2
    python scripts/dev_setup.py

    # python 3
    python3 scripts/dev_setup.py
    ```

1. Verify that the CLI has been installed correctly:

    ```bash
    mvnfeed -h
    ```

## Configuration

The configuration file for the _MvnFeed CLI_ is stored in the file `~/.mvnfeed/mvnfeed.ini` and can be edited manually, but the CLI also provides methods to add/remove configuration values.

1. set the directory where artifacts will be saved once downloaded:

    ```bash
    mvnfeed config stage_dir set --path /tmp/artifacts
    ```

1. add a repository:

    ```bash
    mvnfeed config repo add \
        --name my_devops_feed \
        --username my_username
        --download_url https://{organization}.pkgs.visualstudio.com/_packaging/{feed}/maven/v1
        --upload_url https://{organization}.pkgs.visualstudio.com/_packaging/{feed}/maven/v1
    ```

    **About authorization**: currently only basic auth is supported but if your repository supports other authentication means, edit the configuration file and directly modify the `authorization` value. This value will be passed unmodified in the Authorization HTTP header.

1. list the configured repositories:

    ```bash
    mvnfeed config repo list
    central
      url : http://central.maven.org/maven2
    jcenter
      url : http://jcenter.bintray.com
    jboss
      url : https://repository.jboss.org/nexus/content/repositories/releases
    clojars
      url : https://repo.clojars.org
    atlassian
      url : https://packages.atlassian.com/maven/public
    google
      url : https://maven.google.com
    my_devops_feed
      url : https://{organization}.pkgs.visualstudio.com/_packaging{feed}/maven/v1
    ```

## Usage

If only a couple of dependencies need to be transferred, you can choose to transfer them one by one:

```bash
mvnfeed artifact transfer \
    --from=[REPO_NAME] \
    --to=[REPO_NAME] \
    --name=[GROUP_ID]:[ARTIFACT_ID]:[VERSION] \
    --transfer_deps
```

where:

* `[REPO_NAME]` is the name of one of the configured repositories;
* `transfer_deps`: when defined, dependencies defined in POM files will also be transferred.

For more than a handful of dependencies, it is best to define them in a file and use the `bulk-transfer` command:

```bash
artifacts artifact bulk-transfer \
    --from=[REPO_NAME] \
    --to=[REPO_NAME] \
    --filename=[FILENAME] \
    --transfer_deps
```

where:

* `[FILENAME]` is the name of a file listing the artifacts in the following format:

    ```file
    {GROUP_ID}:{ARTIFACT_ID}:{TYPE}[:{ARCHITECTURE}]:{VERSION}
    ```

* `transfer_deps`: when defined, dependencies defined in POM files will also be transferred.

For example:

```file
org.projectlombok:lombok:jar:1.18.2
com.microsoft.azure:azure-dependencies-bom:pom:1.0.0.M4
org.elasticsearch:elasticsearch:test-jar:tests:2.4.4
io.netty:netty-transport-native-epoll:jar:linux-x86_64:4.1.28.Final
```

## Important notes

* detail information about the transfer can be found in the `mvnfeed.log` logfile created in the current directory;

* because it is not possible to delete uploaded artifacts, mvnfeed tries not to be too clever when parsing the POM files (like deducting versions from `dependencyManagement` block and such.) As a result, you may see following output on the console:

    ```bash
    missing explicit version for jmock:jmock in hamcrest-parent-1.1.pom. Skipping
    ```

    this means that you will have to look at the given POM file and manually upload the skipped dependency, if necessary.

* when BOM (Bill of Materials) files are missing, they can be transferred by defining a POM dependency: `[group_id]:[artifact_id]-bom:pom:[version]`

## Recommanded workflow

Because you may encounter a _very_ large number of missing versions, it is advised to first list the exact dependencies that must be transferred:

1. create a Gradle/Maven project that only includes the desired dependencies;

1. get the list of all transitive dependencies:

    ```bash
    # gradle
    ./gradlew dependencies > dependencies.txt

    # maven
    mvn dependency:list -DoutputFile=dependencies.txt
    ```

1. use mvnfeed to do some cleanup:

    ```bash
    # gradle
    mvnfeed input cleanup \
        --type=gradle \
        --input_file=dependencies.txt \
        --ouput_file=dependencies_cleanup.txt

    # maven
    mvnfeed input cleanup \
        --type=maven \
        --input_file=dependencies.txt \
        --ouput_file=dependencies_cleanup.txt
    ```

1. transfer the dependencies (without the `--transfer_deps` flag):

    ```bash
    artifacts artifact bulk-transfer \
        --from=[REPO_NAME] \
        --to=[REPO_NAME] \
        --filename=dependencies_cleanup.txt
    ```

## Feedback

If you have any issues, questions, comments, or feature requests regarding this tool, please file an issue within this Github repo using our contribution guidelines.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

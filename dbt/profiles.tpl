projet_m2_bi:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: "${project}"
      dataset: ${dev_dataset}
      keyfile: "${sa_key_path}"
      threads: 1
      location: ${region}

    prod:
      type: bigquery
      method: service-account
      project: "${project}"
      dataset: ${prod_dataset}
      keyfile: "${sa_key_path}"
      threads: 4
      location: ${region}


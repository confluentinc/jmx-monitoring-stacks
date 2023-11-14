terraform {
  # Require Terraform version 1.0 (recommended)
  required_version = "~> 1.0"

  # Require the latest 2.x version of the New Relic provider
  required_providers {
    newrelic = {
      source  = "newrelic/newrelic"
    }
  }
}

provider "newrelic" {
  account_id = vars.account_id   # Your New Relic account ID
  api_key = vars.user_key # Your New Relic user key
  region = vars.region        # US or EU (defaults to US)
}

resource "newrelic_one_dashboard_json" "cc_dashboard" {
     json = file("${path.module}/dashboards/cc-dashboard.json")
}

resource "newrelic_entity_tags" "cc_dashboard" {
	guid = newrelic_one_dashboard_json.cc_dashboard.guid
	tag {
    	     key    = "terraform"
    	     values = [true]
	}
}

output "cc_dashboard" {
      value = newrelic_one_dashboard_json.cc_dashboard.permalink
}

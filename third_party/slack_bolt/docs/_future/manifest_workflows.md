---
title: Manifest workflows
order: 4
slug: manifest-workflows
lang: en
layout: future
---

<div class="section-content">

Your app can use Functions by referencing them in Workflows. Your <a href="https://api.slack.com/future/functions/custom" target="_blank">Custom Functions</a> and the <a href="https://api.slack.com/future/functions" target="_blank">Built-in Functions</a> can be used as steps in Workflow definitions.

Workflows are invoked by <a href="https://api.slack.com/future/triggers" target="_blank">Triggers</a>. You will need to set up a Trigger in order to use your defined workflows. Triggers, Workflows, and Functions work together in the following way:

Trigger → Workflow → Workflow Step → Function

Your App Manifest, found at `manifest.json`, is where you will define your workflows.

<table id="workflows">
  <tr>
    <th><h5>workflows</h5></th>
    <th>dictionary</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>key</code></b></td>
    <td>string</td>
    <td>defines the workflow's <code>id</code></td>
  </tr>
  <tr>
    <td><b><code>value</code></b></td>
    <td><a href="#workflow">workflow</a></td>
    <td>defines the function</td>
  </tr>
</table>

<table id="workflow">
  <tr>
    <th><h5>workflow</h5></th>
    <th>object</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>title</code></b></td>
    <td>string</td>
    <td>defines the title</td>
  </tr>
  <tr>
    <td><b><code>description</code></b></td>
    <td>string</td>
    <td>defines the description</td>
  </tr>
  <tr>
    <td><b><code>input_parameters</code></b></td>
    <td><a href="#parameters">parameters</a></td>
    <td>defines the inputs</td>
  </tr>
  <tr>
    <td><b><code>steps</code></b></td>
    <td>list[<a href="#parameters">parameters</a>]</td>
    <td>defines the steps</td>
  </tr>
</table>

<table id="step">
  <tr>
    <th><h5>step</h5></th>
    <th>object</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>id</code></b></td>
    <td>string</td>
    <td>defines the order of the steps</td>
  </tr>
  <tr>
    <td><b><code>function_id</code></b></td>
    <td>string</td>
    <td>identifies the <code>function</code> to evoke</td>
  </tr>
  <tr>
    <td><b><code>inputs</code></b></td>
    <td>dict[string:string]</td>
    <td>defines the inputs to provide to the function</td>
  </tr>
</table>

</div>

<div>
<span class="annotation">Refer to <a href="https://github.com/slack-samples/bolt-python-starter-template/blob/future/manifest.json" target="_blank">our template project</a> to view a full version of <code>manifest.json</code>.</span>
```json
  "workflows": {
    "sample_workflow": {
      "title": "Sample workflow",
      "description": "A sample workflow",
      "input_parameters": {
        "properties": {
          "channel": {
            "type": "slack#/types/channel_id"
          }
        },
        "required": [
          "channel"
        ]
      },
      "steps": [
        {
          "id": "0",
          "function_id": "#/functions/sample_function",
          "inputs": {
            "message": "{{inputs.channel}}"
          }
        },
        {
          "id": "1",
          "function_id": "slack#/functions/send_message",
          "inputs": {
            "channel_id": "{{inputs.channel}}",
            "message": "{{steps.0.updatedMsg}}"
          }
        }
      ]
    }
  }
```
</div>

<details class="secondary-wrapper" >
  
<summary id="built-in-functions" class="section-head" markdown="0">
  <h4 class="section-head">Built-in functions</h4>
</summary>

<div class="secondary-content">
Slack provides built-in functions that can be used by a Workflow to accomplish simple tasks. You can add these functions to your workflow steps in order to use them.

- <a href="https://api.slack.com/future/functions#send-message" target="_blank">Send message</a>
- <a href="https://api.slack.com/future/functions#open-a-form" target="_blank">Open a form</a>
- <a href="https://api.slack.com/future/functions#create-channel" target="_blank">Create channel</a>

Refer to <a href="https://api.slack.com/future/functions" target="_blank">the built-in functions document</a> to learn about the available built-in functions.
</div>

```json
    "$comment": "A step to post the user name to a channel"
    "steps": [
      {
        "id": "0",
        "function_id": "slack#/functions/send_message",
        "inputs": {
          "channel_id": "{{inputs.channel}}",
          "message": "{{inputs.user_name}}"
        }
      }
    ]
```

</details>
